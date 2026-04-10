#             __________               __   ___.
#   Open      \______   \ ____   ____ |  | _\_ |__   _______  ___
#   Source     |       _//  _ \_/ ___\|  |/ /| __ \ /  _ \  \/  /
#   Jukebox    |    |   (  <_> )  \___|    < | \_\ (  <_> > <  <
#   Firmware   |____|_  /\____/ \___  >__|_ \|___  /\____/__/\_ \
#                     \/            \/     \/    \/            \/
# $Id$
#

PUZZLES_SRCDIR = $(APPSDIR)/plugins/puzzles
PUZZLES_OBJDIR = $(BUILDDIR)/apps/plugins/puzzles

PUZZLES_SHARED_SRC = $(call preprocess, $(PUZZLES_SRCDIR)/SOURCES)
PUZZLES_SHARED_OBJ = $(call c2obj, $(PUZZLES_SHARED_SRC))

PUZZLES_GAMES_SRC = $(call preprocess, $(PUZZLES_SRCDIR)/SOURCES.games)
PUZZLES_GAMES_OBJ = $(call c2obj, $(PUZZLES_GAMES_SRC))

PUZZLES_HELP_SRC = $(wildcard $(PUZZLES_SRCDIR)/help/*)
PUZZLES_HELP_OBJ = $(call c2obj, $(PUZZLES_HELP_SRC))

PUZZLES_SRC = $(PUZZLES_GAMES_SRC) $(PUZZLES_SHARED_SRC) $(PUZZLES_HELP_SRC)
PUZZLES_OBJ = $(call c2obj, $(PUZZLES_SRC))

PUZZLES_FINISHED_GAMES = $(basename $(notdir $(filter-out $(PUZZLES_SRCDIR)/src/unfinished/%.c,$(PUZZLES_GAMES_SRC))))
PUZZLES_UNFINISHED_GAMES = $(basename $(notdir $(filter $(PUZZLES_SRCDIR)/src/unfinished/%.c,$(PUZZLES_GAMES_SRC))))

PUZZLES_ROCKS = $(addprefix $(PUZZLES_OBJDIR)/sgt-, $(notdir $(PUZZLES_GAMES_SRC:.c=.rock)))

OTHER_SRC += $(PUZZLES_SRC)
OTHER_INC += -I$(PUZZLES_SRCDIR)/src -I $(PUZZLES_SRCDIR)

ROCKS += $(PUZZLES_ROCKS)

PUZZLES_OPTIMIZE = -O2

ifeq ($(MODELNAME), sansac200v2)
PUZZLES_OPTIMIZE = -Os # tiny plugin buffer
endif

# we suppress all warnings with -w
PUZZLESFLAGS = -I$(PUZZLES_SRCDIR)/dummy $(filter-out			\
		-O%,$(PLUGINFLAGS)) $(PUZZLES_OPTIMIZE)			\
		-Wno-unused-parameter -Wno-sign-compare			\
		-Wno-strict-aliasing -DFOR_REAL				\
		-I$(PUZZLES_SRCDIR)/src -I$(PUZZLES_SRCDIR) -include	\
		$(PUZZLES_SRCDIR)/rbcompat.h -ffunction-sections	\
		-fdata-sections -w -Wl,--gc-sections

define PUZZLE_LINK_RULE
$(PUZZLES_OBJDIR)/sgt-$(1).rock: $(PUZZLES_OBJDIR)/$(2)/$(1).o $(PUZZLES_OBJDIR)/help/$(1).o $(PUZZLES_SHARED_OBJ) $(TLSFLIB)
	$$(SILENT)mkdir -p $$(dir $$@)
	$$(call PRINTS,LD $$(@F))$$(CC) $$(PLUGINFLAGS) -o $(PUZZLES_OBJDIR)/$(1).elf \
		$$(filter %.o, $$^) \
		$$(filter %.a, $$+) \
		-lgcc $$(filter-out -Wl%.map, $$(PLUGINLDFLAGS)) -Wl,$$(LDMAP_OPT),$(PUZZLES_OBJDIR)/src/$(1).map
	$$(SILENT)$$(call objcopy_plugin,$(PUZZLES_OBJDIR)/$(1).elf,$$@)
endef

$(foreach game,$(PUZZLES_FINISHED_GAMES),$(eval $(call PUZZLE_LINK_RULE,$(game),src)))
$(foreach game,$(PUZZLES_UNFINISHED_GAMES),$(eval $(call PUZZLE_LINK_RULE,$(game),src/unfinished)))

$(PUZZLES_SRCDIR)/rbcompat.h:	$(APPSDIR)/plugin.h			\
				$(APPSDIR)/plugins/lib/pluginlib_exit.h	\
				$(BUILDDIR)/sysfont.h			\
				$(PUZZLES_SRCDIR)/rbassert.h		\
				$(TLSFLIB_DIR)/src/tlsf.h \
				$(BUILDDIR)/lang_enum.h

# special pattern rule for compiling puzzles with extra flags
$(PUZZLES_OBJDIR)/%.o: $(PUZZLES_SRCDIR)/%.c $(PUZZLES_SRCDIR)/puzzles.make $(PUZZLES_SRCDIR)/rbcompat.h
	$(SILENT)mkdir -p $(dir $@)
	$(call PRINTS,CC $(subst $(ROOTDIR)/,,$<))$(CC) -I$(dir $<) $(PUZZLESFLAGS) -c $< -o $@
